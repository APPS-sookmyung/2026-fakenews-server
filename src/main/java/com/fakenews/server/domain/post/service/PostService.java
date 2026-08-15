package com.fakenews.server.domain.post.service;

import com.fakenews.server.domain.post.dto.PostRegisterReqDto;
import com.fakenews.server.domain.post.dto.PostReadResDto;
import com.fakenews.server.domain.post.dto.PostRegisterResDto;
import com.fakenews.server.domain.post.entity.Post;
import com.fakenews.server.domain.post.repository.PostRepository;
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

    @Transactional
    public PostRegisterResDto register(PostRegisterReqDto postRegisterReqDto){
        Post post = modelMapper.map(postRegisterReqDto, Post.class);

        return PostRegisterResDto.builder()
                .postId(postRepository.save(post).getPostId())
                .build();
    }

    public PostReadResDto read(Long postId){
        Optional<Post> result = postRepository.findById(postId);
        Post post = result.orElseThrow();
        return modelMapper.map(post, PostReadResDto.class);
    }
}
