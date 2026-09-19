package com.fakenews.server.domain.post.service;

import com.fakenews.server.domain.post.dto.PostRegisterReqDto;
import com.fakenews.server.domain.post.dto.PostReadResDto;
import com.fakenews.server.domain.post.dto.PostRegisterResDto;
import com.fakenews.server.domain.post.entity.Post;
import com.fakenews.server.domain.post.repository.PostRepository;
import com.fakenews.server.domain.auth.UserRepository;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.modelmapper.ModelMapper;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
@RequiredArgsConstructor
public class PostService {
    private final ModelMapper modelMapper;
    private final PostRepository postRepository;
    private final UserRepository userRepository;

    @Transactional
    public PostRegisterResDto register(PostRegisterReqDto postRegisterReqDto, String email){
        var user = userRepository.findByEmail(email)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "인증이 필요합니다."));
        Post post = Post.create(postRegisterReqDto.getContent(), user.getId());

        return PostRegisterResDto.builder()
                .postId(postRepository.save(post).getPostId())
                .build();
    }

    public PostReadResDto read(Long postId){
        Optional<Post> result = postRepository.findById(postId);
        Post post = result.orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "게시글을 찾을 수 없습니다."));
        return modelMapper.map(post, PostReadResDto.class);
    }
}
